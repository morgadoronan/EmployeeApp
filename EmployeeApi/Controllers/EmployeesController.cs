using EmployeeApi.Data;
using EmployeeApi.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System.Text.RegularExpressions;

namespace EmployeeApi.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class EmployeesController : ControllerBase
    {
        private readonly AppDbContext _context;
        private const string AuthToken = "Bearer mysecrettoken";

        public EmployeesController(AppDbContext context)
        {
            _context = context;
        }

        private bool IsAuthorized()
        {
            var token = Request.Headers["Authorization"].FirstOrDefault();
            return token == AuthToken;
        }

        // GET: api/employees
        [HttpGet]
        public async Task<IActionResult> GetEmployees()
        {
            if (!IsAuthorized()) return Unauthorized();
            var employees = await _context.Employees.ToListAsync();
            return Ok(employees);
        }

        // GET: api/employees/{id}
        [HttpGet("{id}")]
        public async Task<IActionResult> GetEmployee(int id)
        {
            if (!IsAuthorized()) return Unauthorized();
            var employee = await _context.Employees.FindAsync(id);
            if (employee == null) return NotFound();
            return Ok(employee);
        }

        // POST: api/employees
        [HttpPost]
        public async Task<IActionResult> CreateEmployee(Employee employee)
        {
            if (!IsAuthorized()) return Unauthorized();
            if (!ModelState.IsValid || !IsValidEmail(employee.Email))
                return BadRequest(ModelState);
            _context.Employees.Add(employee);
            await _context.SaveChangesAsync();
            return CreatedAtAction(nameof(GetEmployee), new { id = employee.Id }, employee);
        }

        // PUT: api/employees/{id}
        [HttpPut("{id}")]
        public async Task<IActionResult> UpdateEmployee(int id, Employee employee)
        {
            if (!IsAuthorized()) return Unauthorized();
            if (id != employee.Id) return BadRequest();
            if (!ModelState.IsValid || !IsValidEmail(employee.Email))
                return BadRequest(ModelState);
            var exists = await _context.Employees.AnyAsync(e => e.Id == id);
            if (!exists) return NotFound();
            _context.Entry(employee).State = EntityState.Modified;
            await _context.SaveChangesAsync();
            return NoContent();
        }

        // DELETE: api/employees/{id}
        [HttpDelete("{id}")]
        public async Task<IActionResult> DeleteEmployee(int id)
        {
            if (!IsAuthorized()) return Unauthorized();
            var employee = await _context.Employees.FindAsync(id);
            if (employee == null) return NotFound();
            _context.Employees.Remove(employee);
            await _context.SaveChangesAsync();
            return NoContent();
        }

        private bool IsValidEmail(string email)
        {
            return Regex.IsMatch(email ?? "", @"^[^@\s]+@[^@\s]+\.[^@\s]+$");
        }
    }
}
